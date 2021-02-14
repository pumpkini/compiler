
class Person {
    string name;
    int age;
    
    void f() {
      Print("our names are:");
    }

    string our_name() {
      Print(age);
      Print(age == this.age);
      f();
      return name + " " +  this.cat.name;
    }

    Cat cat;

    void set_cat(Cat catt) {
      catt.meow();
      this.cat = catt;
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
    c.name = "pishi";
    p = new Person;
    p2 = new Person;
    p.set_cat(c);
    Print(p.cat == new Cat);
    Print(p.cat != new Cat);
    Print(new Cat == p.cat);
    Print(p.cat == c);
    Print(c != p.cat);
    Print(p2.cat == null);
    Print(null != p2.cat);
}
