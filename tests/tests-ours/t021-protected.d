class A {
    protected int valA;   
}

class B extends A{
    int valB;

    void set_valA(){
        this.valA = 10;
    }
}


int main() {
    B b;
    A a;
    a = new A;
    b = new B;
    b.set_valA();
    Print(b.valA);

}