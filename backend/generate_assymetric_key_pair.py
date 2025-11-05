import os
from pathlib import Path
from typing import Literal, Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519

AlgorithmType = Literal["RS256", "RS384", "RS512", "ES256", "ES384", "EdDSA"]

KEY_DIR = Path("./keys")
KEY_DIR.mkdir(parents=True, exist_ok=True)


def generate_keypair(algorithm: AlgorithmType) -> Tuple[bytes, bytes]:
    """Generate private/public keypair for given JWT algorithm."""
    if algorithm.startswith("RS"):
        key_size = {"RS256": 2048, "RS384": 3072, "RS512": 4096}[algorithm]
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    elif algorithm.startswith("ES"):
        curve = ec.SECP256R1() if algorithm == "ES256" else ec.SECP384R1()
        private_key = ec.generate_private_key(curve)
    elif algorithm == "EDDSA":
        private_key = ed25519.Ed25519PrivateKey.generate()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_pem, public_pem


def write_keys(private_pem: bytes, public_pem: bytes, algo: str):
    """Write generated keypair to files with algorithm suffix."""
    private_path = KEY_DIR / f"jwt_private_{algo.lower()}.pem"
    public_path = KEY_DIR / f"jwt_public_{algo.lower()}.pem"

    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)

    try:
        os.chmod(private_path, 0o600)
        os.chmod(public_path, 0o644)
    except Exception:
        pass

    print(f"\n✅ Keys generated successfully for {algo}:")
    print(f"   → Private key: {private_path}")
    print(f"   → Public key:  {public_path}\n")


def main():
    print("=== JWT Key Generator ===")
    print("Supported algorithms: RS256, RS384, RS512, ES256, ES384, EdDSA")
    algo = input("Enter algorithm to generate key for: ").strip().upper()

    try:
        private_pem, public_pem = generate_keypair(algo)  # type: ignore
        write_keys(private_pem, public_pem, algo)
    except ValueError as e:
        print(f"❌ {e}")
    except KeyboardInterrupt:
        print("\nAborted by user.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
