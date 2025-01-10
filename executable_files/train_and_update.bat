@echo off
set HYPERPARAMETER=False
set UPDATE=True

python -m src.train_predict_jobs %HYPERPARAMETER% %UPDATE%

set /p OUTPUT=<temp/prev_and_new_versions.txt

for /f "tokens=1,2 delims=," %%A in ("%OUTPUT%") do (
    set OLD_MODEL_VERSION=%%A
    set NEW_MODEL_VERSION=%%B
)

echo Old Model Version: %OLD_MODEL_VERSION%
echo New Model Version: %NEW_MODEL_VERSION%

for /f %%i in ('git rev-parse HEAD') do set GIT_COMMIT_HASH=%%i

python -m src.management_model_detail_log %NEW_MODEL_VERSION% %GIT_COMMIT_HASH%

git commit -a -m "Training : %NEW_MODEL_VERSION%"
git push

echo Script completed successfully.
exit /b 0
