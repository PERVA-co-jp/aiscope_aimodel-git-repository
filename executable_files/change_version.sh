#!/bin/bash

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

pyenv activate ai-py-venv

export PYTHONPATH=$(pwd)

echo "バージョンIDの入力:"
read -r model_version

python -m src.management_model_change "$model_version"

IFS=',' read -r OLD_MODEL_VERSION NEW_MODEL_VERSION <<< "$OUTPUT"

echo "Old Model Version: $OLD_MODEL_VERSION"
echo "New Model Version: $NEW_MODEL_VERSION"

git commit -a -m "Model Version Change: $NEW_MODEL_VERSION"
git push