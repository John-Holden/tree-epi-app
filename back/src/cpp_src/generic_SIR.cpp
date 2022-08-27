// SIR model re-written in cpp
#include <iostream>
#include <string>
#include "SIR.h"
#include "common.h"
#include <fstream>
#include <jsoncpp/json/json.h>
#include <vector>
#include <tuple>

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
            vector<int> R0generation(pos_x.size(), 0); // time becoming infected
            vector <int> infectionCount(pos_x.size(), 0 ); // number of infections

            bool exceededSteps = false;
            int hostNumber = pos_x.size();
            int steps = ParamRoot["runtime"]["steps"].asInt();

            // initialise R0 generation 
            for (int index=0;  index<R0generation.size(); index++) {
                if (stat[index] != 2) {
                    continue;
                }
                R0generation[index] = 1;
            }

            // iterate over steps
            cout << "[i] Computing " << steps << " steps" << endl;
            for (int t=0; t<steps; t++){
                set <int> newInfected;
                vector <int> newR0gen, newInfCount;

                S.push_back(susceptibleNumber(stat));
                I.push_back(infectedNumber(stat));
                R.push_back(removedNumber(stat));

                writeFieldInt(stat, string(SimInputPath) + "/stat_" + frameLabel(t) + ".csv");                                            

                // update removed status
                vector<int> newRem = getNewRemoved(t, inf_l, inf_l_count, stat);
                for (auto index : newRem) {
                    stat[index] = 3;
                    }   

                if (isExinction(stat)) {
                    cout << "[i] Exiting, no infecteds remain @t " << t + 1 << endl;
                    break;
                }

                // update infection status
                tie(newInfected, newR0gen, newInfCount) = getNewInfected(pos_x, pos_y, inf_l, stat, ParamRoot, R0generation);

                // newly infected
                for (auto index : newInfected) {
                    stat[index] = 2;
                    inf_l_count[index] = t;
                    }

                for (int index=0; index<hostNumber; index++){
                    // update infected generations
                    if (newR0gen[index]) {
                        R0generation[index] = newR0gen[index];
                    }
                    // update infected count
                    if (newInfCount[index]) {
                        infectionCount[index] += newInfCount[index];
                    }
                }
                
                if (isTimeHorizon(t, steps)) {
                    cout << "[i] Exiting, exceeded the time horizon @t " << t + 1 << endl;
                    exceededSteps = true;
                   }
            }

            cout << "[i] Finished computing simulation." << endl;
            writeEnd(SimInputPath);
            // process R0 infection count gen
            vector <float> R0avg;
            R0avg = getAvgR0(R0generation, infectionCount);                       
            writeFieldFloat(R0avg, string(SimInputPath) + "/R0_avg.csv");
            // save SIR
            writeFieldInt(S, string(SimInputPath) + "/S_t.csv");
            writeFieldInt(I, string(SimInputPath) + "/I_t.csv");
            writeFieldInt(R, string(SimInputPath) + "/R_t.csv");     

            return 0;
        }
};


extern "C" {
    Simulation* newSimOjb(){ return new Simulation(); }
    int execute(Simulation* simulation, char* SimPath){ return simulation->Execute(SimPath); }
    }
// 