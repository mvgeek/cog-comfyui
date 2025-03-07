import subprocess
import time
import os
import requests
from weights_manifest import WeightsManifest


class WeightsDownloader:
    supported_filetypes = [
        ".ckpt",
        ".safetensors",
        ".pt",
        ".pth",
        ".bin",
        ".onnx",
        ".torchscript",
        ".engine",
        ".patch",
        ".cube",
    ]

    def __init__(self):
        self.weights_manifest = WeightsManifest()
        self.weights_map = self.weights_manifest.weights_map
        # Hugging Face token for authenticated downloads - read from environment
        self.hf_token = os.environ.get("HF_TOKEN", "")
        if not self.hf_token:
            print("Warning: HF_TOKEN environment variable not set. Some downloads may fail.")

    def get_canonical_weight_str(self, weight_str):
        return self.weights_manifest.get_canonical_weight_str(weight_str)

    def get_weights_by_type(self, type):
        return self.weights_manifest.get_weights_by_type(type)

    def download_weights(self, weight_str):
        if weight_str in self.weights_map:
            if self.weights_manifest.is_non_commercial_only(weight_str):
                print(
                    f"⚠️  {weight_str} is for non-commercial use only. Unless you have obtained a commercial license.\nDetails: https://github.com/replicate/cog-comfyui/blob/main/weights_licenses.md"
                )

            if isinstance(self.weights_map[weight_str], list):
                for weight in self.weights_map[weight_str]:
                    self.download_if_not_exists(
                        weight_str, weight["url"], weight["dest"], weight.get("source")
                    )
            else:
                self.download_if_not_exists(
                    weight_str,
                    self.weights_map[weight_str]["url"],
                    self.weights_map[weight_str]["dest"],
                    self.weights_map[weight_str].get("source")
                )
        else:
            # Check if it's a special model that needs direct handling
            special_models = [
                "flux1-dev.safetensors", 
                "ae.safetensors", 
                "Kasabulibaas.safetensors",
                "flux_realism_lora.safetensors"
            ]
            
            if weight_str in special_models:
                self.download_flux_model(weight_str)
            else:
                raise ValueError(
                    f"{weight_str} unavailable. View the list of available weights: https://github.com/replicate/cog-comfyui/blob/main/supported_weights.md"
                )

    def check_if_file_exists(self, weight_str, dest):
        if dest.endswith(weight_str):
            path_string = dest
        else:
            path_string = os.path.join(dest, weight_str)
        return os.path.exists(path_string)

    def download_if_not_exists(self, weight_str, url, dest, source=None):
        if self.check_if_file_exists(weight_str, dest):
            print(f"✅ {weight_str} exists in {dest}")
            return
        
        if source == "huggingface":
            self.download_from_huggingface(weight_str, url, dest, self.hf_token)
        else:
            WeightsDownloader.download(weight_str, url, dest)

    def download_flux_model(self, weight_str):
        """Download FLUX models from Hugging Face with authentication"""
        if weight_str == "flux1-dev.safetensors":
            dest_dir = "ComfyUI/models/unet"
            url = "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors"
            # Use the token for FLUX models
            token = self.hf_token
        elif weight_str == "ae.safetensors":
            dest_dir = "ComfyUI/models/vae"
            url = "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors"
            # Use the token for FLUX models
            token = self.hf_token
        elif weight_str == "Kasabulibaas.safetensors":
            dest_dir = "ComfyUI/models/loras"
            url = "https://huggingface.co/mvgeek/kasab/resolve/main/Kasabulibaas.safetensors"
            # Use the personal token for private Kasabulibaas LoRA
            token = os.environ.get("HF_PRIVATE_TOKEN", "")
            if not token:
                print("Warning: HF_PRIVATE_TOKEN environment variable not set. Download may fail.")
        elif weight_str == "flux_realism_lora.safetensors":
            # For Civitai downloads, we'll use direct download
            dest_dir = "ComfyUI/models/loras"
            url = "https://civitai.com/api/download/models/706528?type=Model&format=SafeTensor"
            return self.download_from_direct_link(weight_str, url, dest_dir)
        else:
            raise ValueError(f"Unknown FLUX model: {weight_str}")
        
        # Create destination directory if it doesn't exist
        os.makedirs(dest_dir, exist_ok=True)
        
        dest_path = os.path.join(dest_dir, weight_str)
        if os.path.exists(dest_path):
            print(f"✅ {weight_str} exists in {dest_dir}")
            return
            
        self.download_from_huggingface(weight_str, url, dest_dir, token)

    def download_from_huggingface(self, weight_str, url, dest, token):
        """Download from Hugging Face with authentication token"""
        print(f"⏳ Downloading {weight_str} from Hugging Face to {dest}")
        
        # Make sure the destination directory exists
        if "/" in weight_str:
            subfolder = weight_str.rsplit("/", 1)[0]
            dest = os.path.join(dest, subfolder)
        os.makedirs(dest, exist_ok=True)
        
        dest_path = os.path.join(dest, os.path.basename(weight_str))
        
        start = time.time()
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            # Get total file size if provided in headers
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Print progress for large files
                        if total_size > 10*1024*1024 and downloaded_size % (5*1024*1024) < 8192:
                            print(f"  Downloaded {downloaded_size / (1024*1024):.1f}MB of {total_size / (1024*1024):.1f}MB")
            
            elapsed_time = time.time() - start
            file_size_bytes = os.path.getsize(dest_path)
            file_size_megabytes = file_size_bytes / (1024 * 1024)
            print(f"✅ {weight_str} downloaded to {dest} in {elapsed_time:.2f}s, size: {file_size_megabytes:.2f}MB")
            
        except Exception as e:
            print(f"❌ Failed to download {weight_str}: {e}")
            if os.path.exists(dest_path):
                os.remove(dest_path)
            raise

    def download_from_direct_link(self, weight_str, url, dest):
        """Download from direct link without authentication"""
        print(f"⏳ Downloading {weight_str} from direct link to {dest}")
        
        # Make sure the destination directory exists
        if "/" in weight_str:
            subfolder = weight_str.rsplit("/", 1)[0]
            dest = os.path.join(dest, subfolder)
        os.makedirs(dest, exist_ok=True)
        
        dest_path = os.path.join(dest, os.path.basename(weight_str))
        
        start = time.time()
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get total file size if provided in headers
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Print progress for large files
                        if total_size > 10*1024*1024 and downloaded_size % (5*1024*1024) < 8192:
                            print(f"  Downloaded {downloaded_size / (1024*1024):.1f}MB of {total_size / (1024*1024):.1f}MB")
            
            elapsed_time = time.time() - start
            file_size_bytes = os.path.getsize(dest_path)
            file_size_megabytes = file_size_bytes / (1024 * 1024)
            print(f"✅ {weight_str} downloaded to {dest} in {elapsed_time:.2f}s, size: {file_size_megabytes:.2f}MB")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {weight_str}: {e}")
            if os.path.exists(dest_path):
                os.remove(dest_path)
            raise

    @staticmethod
    def download(weight_str, url, dest):
        if "/" in weight_str:
            subfolder = weight_str.rsplit("/", 1)[0]
            dest = os.path.join(dest, subfolder)
            os.makedirs(dest, exist_ok=True)

        print(f"⏳ Downloading {weight_str} to {dest}")
        start = time.time()
        subprocess.check_call(
            ["pget", "--log-level", "warn", "-xf", url, dest], close_fds=False
        )
        elapsed_time = time.time() - start
        try:
            file_size_bytes = os.path.getsize(
                os.path.join(dest, os.path.basename(weight_str))
            )
            file_size_megabytes = file_size_bytes / (1024 * 1024)
            print(
                f"✅ {weight_str} downloaded to {dest} in {elapsed_time:.2f}s, size: {file_size_megabytes:.2f}MB"
            )
        except FileNotFoundError:
            print(f"✅ {weight_str} downloaded to {dest} in {elapsed_time:.2f}s")

    def delete_weights(self, weight_str):
        if weight_str in self.weights_map:
            weight_path = os.path.join(self.weights_map[weight_str]["dest"], weight_str)
            if os.path.exists(weight_path):
                os.remove(weight_path)
                print(f"Deleted {weight_path}") 