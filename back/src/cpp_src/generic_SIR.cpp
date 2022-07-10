// SIR model re-written in cpp
#include <iostream>
#include <string>
#include "SIR.h"
#include "common.h"
#include <fstream>
#include <jsoncpp/json/json.h>
#include <vector>

using namespace std;
using std::vector;

class Simulation{
    
    public: int Execute(char* SimInputPath){ 
            Json::Value ParamRoot {LoadJson(SimInputPath)};
            vector<vector<int>> S {LoadS(SimInputPath)};
            vector<vector<int>> I {LoadI(SimInputPath)};
            vector<vector<int>> R {LoadR(SimInputPath)};
            return 0;
        }
};


extern "C" {
    Simulation* newSimOjb(){ return new Simulation(); }
    int execute(Simulation* simulation, char* SimPath){ return simulation->Execute(SimPath); }
    }
