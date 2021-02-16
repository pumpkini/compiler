
class Car {
    string name;
    int age;
    Engine eng;
    

    void test(){
        Print("Name ",this.name," Engine is ",this.eng.name," NO is ",this.eng.no.name);
        this.eng.no.func(3);
    }



}

class Engine {
    string name;
    NO no;

    string engine_name(){
        return this.name;
    }

    
}


class NO {
    string name;

    void func(int i){
        Print("i is ",i);
    }
}

int main() {
    Car car;
    Engine eng;
    NO no;
    car = new Car;
    eng = new Engine;
    no = new NO;
    car.name = "samand";
    eng.name = "one";
    no.name = "sub";
    eng.no = no;
    car.eng = eng;

    car.test();
    
}
