int main() {
    int a;
    for (a = 0; a < 5; a = a + 1) {
        Print(a);
    }
    
    a = 10;
    for (; a >= 0; a = a - 2) {
        Print(a);
        a = a - 1;
    }
    
    for (a = 100; a < 500;) {
        Print(a);
        a = a + 100;
    }
    
    a = 1;
    for (; a <= 1024;) {
        Print(a);
        a = a * 2;
    }

    for(a = 100; a > 0; a = a / 2) 
    {
        Print(a);
    }
    
}
