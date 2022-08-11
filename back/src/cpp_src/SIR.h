#include <string>
#include <iostream>
#include <sstream>
#include <fstream>
#include <jsoncpp/json/json.h>
#include <math.h>       /* sqrt */

using namespace std; // use all std object names etc. 
using std :: vector;
// Convert Json struct values to output of desired type, e.g. call JsonToInt(json_obj["o"]
int JsonToInt(Json::Value value) {return std:: stoi(value.toStyledString());}
float JsonToFloat(Json::Value value) {return std:: stof(value.toStyledString());}
double JsonToDouble(Json::Value value) {return std:: stod(value.toStyledString());}


// print a vector
void PrintVect1 (const vector<int>& v){
  //vector<int> v;
  for (int i=0; i<v.size();i++){
    cout << v[i] << endl;
  }
}


int pow2(int num) {
    return num * num;
}


float getDistance(int x1, int y1, int x2, int y2) {
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
vector <int> evolveStep(vector <int> xPos, vector <int> yPos, vector <int> Ilt, vector <int> stat, Json::Value simContext) {
    cout << "[i] Evolving step..." << endl;
    cout << simContext << endl;
    
    int num_hosts = xPos.size();
    vector <int> newInfected(xPos.size(), 0);
    
    // Fields have values: S == 1 && I == 2 && R == 3
    for (int index=0; index<num_hosts; index++) {
        if ( stat[index] != 2 ) {
            // Skip anything not infected
            continue;  
        }
        
        cout << "we have infected @ "  << endl;
        cout << xPos[index] << " " <<yPos[index] << endl;

        // get new infections due to infected tree
        for (int index1=0; index1<num_hosts; index1++) {
            cout << "[i] Finding new infections due to I_index" << endl;
            
            if ( index1 == index  ) {
                // Skip self-infections
                continue;  
            }

            if (stat[index1] == 2) {
                // skip other infections - cannot re-infect infected
                continue;
            }

            // work out transitions (S_i --> I_i) due to I_index
            float dist = getDistance(xPos[index], xPos[index1], yPos[index], yPos[index1]);
            float pr = infectionPr(dist, simContext["dispersal"], simContext["epidemic_params"]);
                        
            if (!isInfected(pr) ) {
                continue;
            }

            // Update state to infectious
            newInfected[index1] = 1;
        }

        cout << "finished index1 loop" << endl;
        PrintVect1(newInfected);
    }

    return vector <int> {0, 1, 2};

}
