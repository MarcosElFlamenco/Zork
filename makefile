MAX_MOVES=3
CURRENT_GAME=lostpig
CURRENT_SUBMISSION=testing_submission


RUN_COMMAND=python run_agent.py -v -n $(MAX_MOVES)  --agent $(CURRENT_SUBMISSION) -g $(CURRENT_GAME) --debug-verbose --print-full-output 

run:
	$(RUN_COMMAND) > results/$(CURRENT_GAME)_$(CURRENT_SUBMISSION).txt

run_err:
	python run_agent.py --agent $(CURRENT_SUBMISSION) --game $(CURRENT_GAME) -v -n $(MAX_MOVES) 2>&1 | head -100

run_with_output:
	$(RUN_COMMAND)
local_run:
	python $(CURRENT_SUBMISSION)/agent.py -v -n $(MAX_MOVES) -g $(CURRENT_GAME) > results/$(CURRENT_GAME)_local.txt