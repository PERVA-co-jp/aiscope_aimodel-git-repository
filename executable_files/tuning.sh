#!/bin/bash

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

pyenv activate ai-py-venv

export PYTHONPATH=$(pwd)

HYPERPARAMETER=True
UPDATE=True

python -m src.train_predict_jobs "$HYPERPARAMETER" "$UPDATE"

if [ -f temp/prev_and_new_versions.txt ]; then
    IFS=',' read -r OLD_MODEL_VERSION NEW_MODEL_VERSION < temp/prev_and_new_versions.txt
else
    echo "Error: temp/prev_and_new_versions.txt not found."
    exit 1
fi

echo "Old Model Version: $OLD_MODEL_VERSION"
echo "New Model Version: $NEW_MODEL_VERSION"

GIT_COMMIT_HASH=$(git rev-parse HEAD)
if [ $? -ne 0 ]; then
    echo "Error: Failed to retrieve Git commit hash."
    exit 1
fi

python -m src.management_model_detail_log "$NEW_MODEL_VERSION" "$GIT_COMMIT_HASH"

# if [ -d "output_train/$OLD_MODEL_VERSION" ]; then
#    rm -rf "output_train/$OLD_MODEL_VERSION"
#    echo "Deleted: output_train/$OLD_MODEL_VERSION"
#else
#    echo "Warning: Directory output_train/$OLD_MODEL_VERSION not found."
#fi

# git rm -r "output_train/$OLD_MODEL_VERSION"
# git add "output_train/$NEW_MODEL_VERSION"
git commit -a -m "Training : $NEW_MODEL_VERSION"
git push
