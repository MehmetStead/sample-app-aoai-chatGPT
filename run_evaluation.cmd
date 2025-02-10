@echo off
echo Running Chat Evaluator...
echo.

:: Change to the project root directory (adjust this path if needed)
cd %~dp0

:: Run the evaluation module correctly
python -m backend.evaluation.test_evaluator

echo.
if %ERRORLEVEL% EQU 0 (
    echo Evaluation completed successfully!
) else (
    echo Evaluation failed with error code %ERRORLEVEL%
)

:: Pause to see the results
pause 