@echo off
REM Registra a tarefa diaria no Agendador de Tarefas do Windows.
REM Execute como Administrador uma unica vez.

set PYTHON=python
set SCRIPT=%~dp0daily_auto.py
set TASK_NAME=YT-Shorts-Daily

echo Registrando tarefa: %TASK_NAME%
echo Script: %SCRIPT%
echo Horario: 06:00 todos os dias

schtasks /create /tn "%TASK_NAME%" /tr "%PYTHON% \"%SCRIPT%\"" /sc DAILY /st 06:00 /f /rl HIGHEST

if %ERRORLEVEL% == 0 (
    echo.
    echo Tarefa criada com sucesso!
    echo O video sera produzido automaticamente as 06:00 todo dia.
    echo Para ver: Agendador de Tarefas ^> %TASK_NAME%
) else (
    echo.
    echo ERRO ao criar tarefa. Execute este .bat como Administrador.
)

pause
