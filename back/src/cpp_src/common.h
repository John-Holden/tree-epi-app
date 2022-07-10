#include <string>
#include <iostream>
#include <fstream>
#include <jsoncpp/json/json.h>
#include <vector>

using namespace std; // use all std object names etc. 
using std :: vector;


void print(string char_seq) {std:: cout << char_seq << std :: endl;}


Json::Value LoadJson(string sim_loc)
{   
    ifstream parameter_input(sim_loc+"/parameters.json");
    Json::Reader reader;
    Json::Value root;
    reader.parse(parameter_input, root);
    return root;
}


vector<int> VectRtrn() 
{   
    vector <int> vect;
    for (int i = 0; i <10; i++) {vect.push_back(i);};
    for (int i: vect) {std :: cout << i << "   ";};
    
    return vect;
}





