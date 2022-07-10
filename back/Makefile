unit_test:
	pytest

 compile_SIR:
	 cd src/cpp_src && \
 	 g++ -c -fPIC generic_SIR.cpp -o generic_SIR.o -ljsoncpp && \
 	 g++ -shared -Wl,-soname,libSIR.so -o libSIR.so  generic_SIR.o -ljsoncpp
