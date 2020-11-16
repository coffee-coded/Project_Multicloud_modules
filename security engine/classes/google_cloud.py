from google.cloud import kms
import base64
import json
import google.cloud.dlp
import os
import secrets
import base64


class gcp_dlp:
    def __init__(self, project_id, location_id, key_id, key_ring_id):
        self.project_id = project_id
        self.location_id = location_id
        self.key_id = key_id
        self.key_ring_id = key_ring_id
        if key_id != "None" and key_ring_id != "None":
            unwrapped_key = secrets.token_bytes(32)
            x = self.encrypt_symmetric(
                key_ring_id, key_id, plaintext_bytes=unwrapped_key)
            self.wrapped_key = x.ciphertext
            self.export_wrap = 0

    def create_key_ring(self, id):
        # Create the client.
        client = kms.KeyManagementServiceClient()

        # Build the parent location name.
        location_name = f'projects/{self.project_id}/locations/{self.location_id}'

        # Build the key ring.
        key_ring = {}

        # Call the API.
        created_key_ring = client.create_key_ring(
            request={'parent': location_name, 'key_ring_id': id, 'key_ring': key_ring})
        # print('Created key ring: {}'.format(created_key_ring.name))
        return created_key_ring

    def create_key_symmetric_encrypt_decrypt(self, key_ring_id, id):
        # Create the client.
        client = kms.KeyManagementServiceClient()

        # Build the parent key ring name.
        key_ring_name = client.key_ring_path(
            self.project_id, self.location_id, key_ring_id)

        # Build the key.
        purpose = kms.CryptoKey.CryptoKeyPurpose.ENCRYPT_DECRYPT
        algorithm = kms.CryptoKeyVersion.CryptoKeyVersionAlgorithm.GOOGLE_SYMMETRIC_ENCRYPTION
        key = {
            'purpose': purpose,
            'version_template': {
                'algorithm': algorithm,
            }
        }

        # Call the API.
        created_key = client.create_crypto_key(
            request={'parent': key_ring_name, 'crypto_key_id': id, 'crypto_key': key})
        # print('Created symmetric key: {}'.format(created_key.name))
        return created_key

    def deidentify_with_redact(self, input_str, info_types):

        project = self.project_id

        # Instantiate a client
        dlp = google.cloud.dlp_v2.DlpServiceClient()
        # Convert the project id into a full resource id.
        parent = f"projects/{project}"
        # Construct inspect configuration dictionary
        inspect_config = {"info_types": [
            {"name": info_type} for info_type in info_types]}

        # Construct deidentify configuration dictionary
        deidentify_config = {
            "info_type_transformations": {
                "transformations": [{"primitive_transformation": {"redact_config": {}}}]
            }
        }
        # Construct item
        item = {"value": input_str}

        # Call the API
        response = dlp.deidentify_content(
            request={
                "parent": parent,
                "deidentify_config": deidentify_config,
                "inspect_config": inspect_config,
                "item": item,
            }
        )

        # Print out the results.
        return response.item.value

    def deidentify_with_replace(self, input_str, info_types, replacement_str="REPLACEMENT_STR"):
        # print(input_str, info_types)
        project = self.project_id
        # print(info_types)
        # Instantiate a client
        dlp = google.cloud.dlp_v2.DlpServiceClient()

        # Convert the project id into a full resource id.
        parent = f"projects/{project}"

        # Construct inspect configuration dictionary
        inspect_config = {"info_types": [
            {"name": info_type} for info_type in info_types]}

        # Construct deidentify configuration dictionary
        deidentify_config = {
            "info_type_transformations": {
                "transformations": [
                    {
                        "primitive_transformation": {
                            "replace_config": {
                                "new_value": {"string_value": replacement_str}
                            }
                        }
                    }
                ]
            }
        }

        # Construct item
        item = {"value": input_str}

        # Call the API
        response = dlp.deidentify_content(
            request={
                "parent": parent,
                "deidentify_config": deidentify_config,
                "inspect_config": inspect_config,
                "item": item,
            }
        )

        # Print out the results.
        # print('Returning ', response.item.value)
        return response.item.value

    def deidentify_with_mask(self, input_str, info_types, masking_character=None, number_to_mask=0):
        project = self.project_id
        # Instantiate a client
        dlp = google.cloud.dlp_v2.DlpServiceClient()

        # Convert the project id into a full resource id.
        parent = f"projects/{project}"

        # Construct inspect configuration dictionary
        inspect_config = {"info_types": [
            {"name": info_type} for info_type in info_types]}

        # Construct deidentify configuration dictionary
        deidentify_config = {
            "info_type_transformations": {
                "transformations": [
                    {
                        "primitive_transformation": {
                            "character_mask_config": {
                                "masking_character": masking_character,
                                "number_to_mask": number_to_mask,
                            }
                        }
                    }
                ]
            }
        }

        # Construct item
        item = {"value": input_str}

        # Call the API
        response = dlp.deidentify_content(
            request={
                "parent": parent,
                "deidentify_config": deidentify_config,
                "inspect_config": inspect_config,
                "item": item,
            }
        )

        # Print out the results.
        return response.item.value

    def encrypt_symmetric(self, key_ring_id, key_id, plaintext_bytes):
        project_id = self.project_id
        location_id = self.location_id
        # plaintext_bytes = plaintext.encode('utf-8')

        # Create the client.
        client = kms.KeyManagementServiceClient()

        # Build the key name.
        key_name = client.crypto_key_path(
            project_id, location_id, key_ring_id, key_id)

        # Call the API.
        encrypt_response = client.encrypt(
            request={'name': key_name, 'plaintext': plaintext_bytes})
        print('Ciphertext: {}'.format(
            base64.b64encode(encrypt_response.ciphertext)))
        return encrypt_response

    def deidentify_with_fpe(
        self,
        input_str,
        info_types,
        key_ring_id,
        key_id,
        name,
        alphabet,
        surrogate_type=None
    ):
        project = self.project_id
        location = self.location_id
        key_name = f"projects/{project}/locations/global/keyRings/{key_ring_id}/cryptoKeys/{key_id}"

        # Storing the wrapped key inside json file
        self.export_wrap = 1

        # Instantiate a client
        dlp = google.cloud.dlp_v2.DlpServiceClient()

        # Convert the project id into a full resource id.
        parent = f"projects/{project}"

        # wrapped_key = base64.b64decode(wrapped_key)

        # Construct FPE configuration dictionary
        crypto_replace_ffx_fpe_config = {
            "crypto_key": {
                "kms_wrapped": {"wrapped_key": self.wrapped_key, "crypto_key_name": key_name}
            },
            "custom_alphabet": alphabet,
        }

        # Add surrogate type
        if surrogate_type:
            crypto_replace_ffx_fpe_config["surrogate_info_type"] = {
                "name": surrogate_type}

        # Construct inspect configuration dictionary
        inspect_config = {"info_types": [
            {"name": info_type} for info_type in info_types]}

        # Construct deidentify configuration dictionary
        deidentify_config = {
            "info_type_transformations": {
                "transformations": [
                    {
                        "primitive_transformation": {
                            "crypto_replace_ffx_fpe_config": crypto_replace_ffx_fpe_config
                        }
                    }
                ]
            }
        }

        # Convert string to item
        item = {"value": input_str}

        # Call the API
        response = dlp.deidentify_content(
            request={
                "parent": parent,
                "deidentify_config": deidentify_config,
                "inspect_config": inspect_config,
                "item": item,

            }
        )

        # Print results
        return response.item.value

    def export_wrap_fn(self, name):
        if self.export_wrap == 1:
            wrapped_keys = {}
            wrapped_key = self.wrapped_key
            wrapped_key = base64.b64encode(wrapped_key)
            try:
                with open('wrapped_keys.json') as f:
                    wrapped_keys = json.load(f)
            except:
                wrapped_keys = {"keys": []}
            wrapped_keys['keys'].append({
                "name": name,
                "key_id": self.key_id,
                "key_ring_id": self.key_ring_id,
                "wrapped_key": wrapped_key.decode()
            })
            with open('wrapped_keys.json', 'w') as f:
                json.dump(wrapped_keys, f)
