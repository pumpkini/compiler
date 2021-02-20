class A {
    private int val;
    public void set_val(){
        this.val = 10;
    }
   
}

class B {
    int val1;
    A a;
    public int val_a(){
        return this.a.val;
    }

}


int main() {
    A a;
    B b;
    a = new A;
    b = new B;
    a.set_val();
    b.a = a;
    Print(b.val_a());

    
}