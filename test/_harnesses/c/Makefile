WARNING_LEVEL := -Weverything
SILENCE_WARNINGS := -Wno-float-equal -Wno-poison-system-directories -Wno-unused-parameter -Wno-padded

play: play.c beschi.h
	clang $(WARNING_LEVEL) $(SILENCE_WARNINGS) -O3 -g -o $@ play.c

.PHONY: clean
clean:
	rm -rf play

.PHONY: check
check: play
	leaks -atExit -- ./play
