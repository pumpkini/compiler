int main() {
    int a;
    int b;
    bool c;
    bool d;
    double e;
    double f;

    a = -234;
    b = 0;
    c = true;
    d = false;
    e = 4.7;
    f = 1252.E-2;
    
    Print(a, " ", itod(a));
    Print(b, " ", itod(b)); 
    Print(itod(5238));

/*
    Print(e, " ", dtoi(e)); // 5
    Print(f, " ", dtoi(f)); // 13
    Print(dtoi(-0.7)); //-1
    Print(dtoi(-0.5)); //0
    Print(dtoi(4.33)); //4
    Print(dtoi(0.5)); //1
    Print(dtoi(-0.1)); //0
*/

    Print(a, " ", itob(a));
    Print(b, " ", itob(b));
    Print(itob(22442));
    
    Print(c, " ", btoi(c));
    Print(d, " ", btoi(d));
    
    //Print(btoi(itob(dtoi(0.1))));
    
}
