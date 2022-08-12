dmc: ../addmc/src/* ../addmc/Makefile
	make -C ../addmc clean-dmc
	make -C ../addmc dmc opt=-Ofast link=-static
	rm -f dmc
	cp ../addmc/dmc .

.PHONY: clean

clean:
	rm -f dmc dmc.sif
