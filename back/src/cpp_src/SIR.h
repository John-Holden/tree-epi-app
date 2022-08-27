#include <string>
#include <iostream>
#include <sstream>
#include <fstream>
#include <jsoncpp/json/json.h>
#include <math.h>       /* sqrt */
#include <set>
#include <tuple>

using namespace std; // use all std object names etc. 
using std :: vector;
// Convert Json struct values to output of desired type, e.g. call JsonToInt(json_obj["o"]
int JsonToInt(Json::Value value) {return std:: stoi(value.toStyledString());}
float JsonToFloat(Json::Value value) {return std:: stof(value.toStyledString());}
double JsonToDouble(Json::Value value) {return std:: stod(value.toStyledString());}


// print a vector
void PrintVect1 (const vector<int>& v){
  for (int i=0; i<v.size();i++){
    cout << v[i] << endl;
  }
}


// print a vector
void PrintSet (const set<int>& s)  {
  for (auto i : s) {
      cout << i << endl;
  }
}


int pow2(int num) {
    return num * num;
}


float getDistance(int x1, int x2, int y1, int y2) {
    return sqrt (pow2(x1 - x2) + pow2(y1 - y2));
}


float gaDispersal(float dist, float dispParam) {
    float exponent = dist / dispParam;
    return exp(-1 * exponent * exponent);

}


// Compute the probability of infection between I and S trees 
float infectionPr(float dist, Json::Value dispersal, Json::Value epiParams){
    
    if (dispersal["model"] != "gaussian") {
        throw std::invalid_argument( "[e] Dispersal type not implemented" );
    }
    
    float dispPr = gaDispersal(dist, dispersal["value"].asFloat());
    return epiParams["beta_pr"].asFloat() * dispPr; 
} 


// Draw samples to determine if infected or not
bool isInfected(float infectPr) {
    float r = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
    if (infectPr > r) {
        return true;
    }
    return false;
}


// Find newly infected trees, return array with update infection states 
std::tuple<set<int>, vector<int>, vector<int>>  getNewInfected(vector <int> xPos, vector <int> yPos, 
                                                  vector <int> Ilt, vector <int> stat, 
                                                  Json::Value simContext, vector <int> R0gen ) {
    
    // init variables     
    int numHosts = xPos.size();
    float dist, pr;
    set<int> newInfected;
    vector<int> newR0gen (stat.size(), 0);
    vector <int> newInfCount(xPos.size(), 0);

    // fields have values: S == 1 && I == 2 && R == 3
    for (int index=0; index<numHosts; index++) {
        //  iterate over infected - i.e. skip anything not infected 
        if ( stat[index] != 2 ) {
            continue;  
        }

        // iterate over susceptibles & get new infections
        for (int index1=0; index1<numHosts; index1++) {
            
            // skip self-infections
            if ( index1 == index  ) {
                continue;  
            }

            // skip anything other than susceptible
            if (stat[index1] != 1 ) {
                continue;
            }

            // work out transitions (S_i --> I_i) due to I_index
            dist = getDistance(xPos[index], xPos[index1], yPos[index], yPos[index1]);
            pr = infectionPr(dist, simContext["dispersal"], simContext["epidemic_params"]);
                        
            if (!isInfected(pr) ) {
                continue;
            }
            
            // new transition S --> I
            newInfected.insert(index1);
            // update R0 gen
            newInfCount[index] += 1;
            newR0gen[index1] = R0gen[index] + 1;
        }
    }

    return {newInfected, newR0gen, newInfCount};
}


// Find new removed trees based on pre-calculated lifetimes
vector<int> getNewRemoved(int t, vector <int> Ilt, vector <int> Ilt_count, vector <int> stat) {
    
    vector<int> newRemoved;
    for (int i=0; i < Ilt.size(); i++) {
    
        // only infecteds transition
        if (stat[i] != 2) {
            continue;
        }

        // only transition at given time
        if (t != Ilt[i] + Ilt_count[i]) {
            continue;
        }

        // otherwise, new transition I --> R
        newRemoved.push_back(i);
    }

    return newRemoved;
}


// True if no infected trees remain
bool isExinction(vector<int> stat) {
    for (int i=0; i<stat.size(); i++) {
        if (stat[i] == 2) {
            return false;
        } 
    }
    return true;
}

// Reached the maximum number of time steps
bool isTimeHorizon(int t, int steps) {
    if (t+1 == steps) {
        return true;
    }
    return false;
}

// count number of infected trees
int infectedNumber(vector<int> stat) {
int count = 0;
for (int i=0; i < stat.size(); i++) {
    if (stat[i] != 2) {
        continue;
    }
    
    count++;
}
return count;
}

// count number of infected trees
int removedNumber(vector<int> stat) {
int count = 0;
for (int i=0; i < stat.size(); i++) {
    if (stat[i] != 3) {
        continue;
    }
    
    count++;
}
return count;
}

// count number of infected trees
int susceptibleNumber(vector<int> stat) {
int count = 0;
for (int i=0; i < stat.size(); i++) {
    if (stat[i] != 1) {
        continue;
    }
    
    count++;
}
return count;
}

// calcualte & return average R0 for each generation
vector <float> getAvgR0(vector<int> R0Gen, vector<int> infCount) {
    int maxGen = 0;
    int maxGenUpper = 50;
    vector <int> R0GenNumb(maxGenUpper, 0);
    vector <int> R0GenCount(maxGenUpper, 0);
    vector <float> avgR0;

    for (int index=0; index < R0Gen.size(); index++) {
        
        // gen 0 means uninfected susceptible
        if (!R0Gen[index]) {
            continue;
        }

        // record maximum generation
        if (R0Gen[index] > maxGen) {
            maxGen = R0Gen[index];
        } 

        // cumulative sum of all infections by generation
        R0GenNumb[R0Gen[index] - 1] += 1;
        R0GenCount[R0Gen[index] - 1] += infCount[index];  
    }
    
    // divide number of secondary infection for generation by number of infecteds
    for (int index=0; index < maxGenUpper; index++) {
        // break at the first zero count
        if ( !R0GenCount[index] ) {
            break;
        }
        
        float avgROgen = static_cast<float> (R0GenCount[index]) / static_cast<float> (R0GenNumb[index]);
        avgR0.push_back(avgROgen);
    }

    return avgR0;
}