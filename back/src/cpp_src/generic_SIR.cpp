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
using std::cout;
using std::endl;

// C++ class - called by Python/C bindings
class Simulation{
    
    public: int Execute(char* SimInputPath){
             
            cout << "[i] Entered into cpp binary. Loading inputs..." << endl;
            Json::Value ParamRoot {LoadJson(SimInputPath)};
            vector<int> pos_x {LoadField( std :: string(SimInputPath) + "/pos_x.csv") };
            vector<int> pos_y {LoadField( std :: string(SimInputPath) + "/pos_y.csv") };
            vector<int> inf_l {LoadField( std :: string(SimInputPath) + "/inf_lt.csv") };
            vector<int> stat {LoadField( std :: string(SimInputPath) + "/stat.csv") };
            vector<int> inf_l_count(pos_x.size(), 0); // time becoming infected
        
            int steps = ParamRoot["runtime"]["steps"].asInt();

            // iterate over steps
            for (int t=0; t<steps; t++){
                cout << "[i] Computing step : " << t << endl;

                // update removed status
                cout << "inf lifetimes before" << endl;
                PrintVect(stat);
                vector<int> newRem = getNewRemoved(t, inf_l, inf_l_count, stat); 
                for (auto index : newRem) {
                    stat[index] = 3;
                    }   
                    
                cout << "after removal" << endl;
                PrintVect(stat);

                // update infection status
                set<int> newInf = getNewInfected(pos_x, pos_y, inf_l, stat, ParamRoot);
                for (auto index : newInf) {
                    stat[index] = 2;
                    inf_l_count[index] = t;
                    }   

                


            }
            


            return 0;
        }
};







extern "C" {
    Simulation* newSimOjb(){ return new Simulation(); }
    int execute(Simulation* simulation, char* SimPath){ return simulation->Execute(SimPath); }
    }
