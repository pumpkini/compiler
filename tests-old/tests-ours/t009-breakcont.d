int main() {
    int a;
    int b;
    int i;

    b = 0;
    for(i = 1; true; i = i + 1) {
        Print("Please enter the #", i, " number:");
        a = ReadInteger();
        if (a < 0)
            continue;
        b = b + a;
        if (a != 0)
          continue;
        else 
          break;
    }

    Print("Sum of positive numbers is: ", b);
}
