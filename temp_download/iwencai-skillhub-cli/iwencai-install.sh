#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INSTALL_BASE="${HOME}/.iwencai-skillhub"
BIN_DIR="${HOME}/.local/bin"
CLI_TARGET="${INSTALL_BASE}/aime_skillhub_cli.py"
WRAPPER_TARGET="${BIN_DIR}/iwencai-skillhub-cli"

install_cli() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required for iwencai-skillhub-cli." >&2
    exit 1
  fi

  mkdir -p "${INSTALL_BASE}" "${BIN_DIR}"
  cp "${SCRIPT_DIR}/aime_skillhub_cli.py" "${CLI_TARGET}"
  chmod +x "${CLI_TARGET}"
  
  # Copy the entire cli directory (including skills_upgrade.py and other dependencies)
  cp -r "${SCRIPT_DIR}/cli" "${INSTALL_BASE}/"

  cat > "${WRAPPER_TARGET}" <<'WRAPPER'
#!/usr/bin/env bash
set -euo pipefail

BASE="${HOME}/.iwencai-skillhub"
CLI="${BASE}/aime_skillhub_cli.py"

if [[ ! -f "${CLI}" ]]; then
  echo "Error: CLI not found at ${CLI}" >&2
  exit 1
fi

exec python3 "${CLI}" "$@"
WRAPPER

  chmod +x "${WRAPPER_TARGET}"
}

install_cli

# Check if ~/.local/bin is in PATH
if [[ "$PATH" != *"$HOME/.local/bin"* ]]; then
    echo "Adding ~/.local/bin to PATH..."
    
    # Determine shell type
    if [[ "$SHELL" == *"zsh"* ]]; then
        PROFILE_FILE="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        PROFILE_FILE="$HOME/.bash_profile"
    else
        PROFILE_FILE="$HOME/.profile"
    fi
    
    # Add to profile file if not already present
    if ! grep -q "export PATH=\"\$HOME/.local/bin:\\$PATH\"" "$PROFILE_FILE"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$PROFILE_FILE"
        echo "Added ~/.local/bin to PATH in $PROFILE_FILE"
        echo "Please restart your terminal or run 'source $PROFILE_FILE' to apply the changes."
    else
        echo "~/.local/bin is already in PATH"
    fi
fi

echo "IWencai Skillhub CLI installation complete."
echo "You can now use 'iwencai-skillhub-cli install abc' to install skills."
echo "Installation path: ${WRAPPER_TARGET}"
