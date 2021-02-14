
class Person {
    string name;
    int age;
    

    string our_name() {
      Print(age);
      Print(age == this.age);
      return name + " " +  this.cat.name;
    }

    Cat cat;
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
    p = new Person;
    p.age = 22;
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
