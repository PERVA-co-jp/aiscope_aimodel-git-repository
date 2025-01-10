@echo off
echo バージョンIDの入力:
set /p MODEL_VERSION=

python -m src.management_model_change %MODEL_VERSION%

for /f "tokens=1,2 delims=," %%A in ("%OUTPUT%") do (
    set OLD_MODEL_VERSION=%%A
    set NEW_MODEL_VERSION=%%B
)

echo Old Model Version: %OLD_MODEL_VERSION%
echo New Model Version: %NEW_MODEL_VERSION%

git commit -a -m "Model Version Change : %NEW_MODEL_VERSION%"
git push