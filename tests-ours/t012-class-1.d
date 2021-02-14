
class Person {
    string name;
    int age;
    Cat cat;

    string our_name() {
      return this.name + " " +  this.cat.name;
    }
}

class Cat {
    string name;
    void meow() {
      Print(this.name + " says meow");
    }
}

int main() {
    Person p;
    Cat c;
    Person p2;
    
    c = new Cat;
    c.name = "saba";
    
    p = new Person;
    p.cat = c;
    p.cat.name = "pishi";
    p.cat.meow();

    p2 = new Person;

    p2.cat = c;
    p2.cat.name = "lilii";
    p.cat.meow();

    p2.cat = new Cat;
    p2.cat.name = "kitti";
    p2.cat.meow();
    p.cat.meow();

    p.name = "Saba";
    Print(p.our_name());
    
}
