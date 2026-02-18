MAX_MOVES=30
CURRENT_GAME=zork3
CURRENT_SUBMISSION=testing_submission

run:
	python run_agent.py -v -n $(MAX_MOVES) --agent $(CURRENT_SUBMISSION) -g $(CURRENT_GAME) | results/$(CURRENT_GAME).txt

run_with_output:
	python run_agent.py -v -n $(MAX_MOVES)  --agent $(CURRENT_SUBMISSION) -g $(CURRENT_GAME)

local_run:
	python $(CURRENT_SUBMISSION)/agent.py -v -n $(MAX_MOVES) -g $(CURRENT_GAME) > results/$(CURRENT_GAME)_local.txt