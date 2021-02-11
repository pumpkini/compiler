int main() {
    int a;
    int b;
    int c;
    bool d;
    
    a = 10;
    b = -3;
    c = 9;

    d = (a > b) != (c < b);

    Print(d);
    Print(a >= c);
    Print(c < a + b);
    Print(a + b > c);
}
