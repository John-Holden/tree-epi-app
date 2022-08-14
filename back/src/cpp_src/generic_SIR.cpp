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
            vector<int> S, I, R;  // record evolution of fields in time

            int steps = ParamRoot["runtime"]["steps"].asInt();
            int hostNumber = pos_x.size();
            bool exceededSteps = false;
            int Snum, Inum, Rnum;

            // iterate over steps
            for (int t=0; t<steps; t++){
                // Snum = susceptibleNumber(stat);
                // Inum = infectedNumber(stat);
                // Rnum = removedNumber(stat);
                // S.push_back(Snum), I.push_back(Inum), R.push_back(Rnum);
                writeField(stat, string(SimInputPath) + "/stat_" + frameLabel(t) + ".csv");                            

                cout << "[i] Computing step : " + frameLabel(t) << endl;

                // update removed status
                vector<int> newRem = getNewRemoved(t, inf_l, inf_l_count, stat);
                for (auto index : newRem) {
                    stat[index] = 3;
                    }   

                if (isExinction(stat)) {
                    cout << "[i] Exiting, no infecteds remain" << endl;
                    break;
                }

                // update infection status
                set<int> newInf = getNewInfected(pos_x, pos_y, inf_l, stat, ParamRoot);
                for (auto index : newInf) {
                    stat[index] = 2;
                    inf_l_count[index] = t;
                    }
                
                if (isTimeHorizon(t, steps)) {
                    cout << "[i] Exiting, exceeded the time horizon" << endl;
                    exceededSteps = true;
                   }
            }

            cout << "[i] Finished computing simulation." << endl;
            writeEnd(SimInputPath);
            // writeField(I, string(SimInputPath) + "/I_t" + ".csv");
            // writeField(R, string(SimInputPath) + "/R_t" + ".csv");                            
            return 0;
        }
};


extern "C" {
    Simulation* newSimOjb(){ return new Simulation(); }
    int execute(Simulation* simulation, char* SimPath){ return simulation->Execute(SimPath); }
    }
// 