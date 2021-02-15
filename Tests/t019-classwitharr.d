class Car {
    string name;
    int age;

    int car_age(){
        return this.age;
    }



}


int main() {
    Car car;
    int[] arr;
    int i;
    car = new Car;
    car.name = "samand";
    car.age = 3;
    arr = NewArray(4,int);
    for(i = 0 ; i < 4 ; i = i + 1){
        arr[i] = i ;
    }
    Print(arr[car.car_age()]);
}
