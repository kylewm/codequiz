#include <iostream>
#include <string>

int evaluate(std::string input)
{
	// TODO
	return -1;
}

// Receives input on a single line from standard in. Computes and
// prints the result on a single line to standard out. For example,
// the input
//
// 11+2*
//
// should yield the result:
//
// 4
int main(int argc, char** argv)
{
	std::string input;
	std::cin >> input;
	int result = evaluate(input);
	std::cout << result << std::endl;
	return 0;
}
