package main

import (
    "encoding/csv"
    "fmt"
    "os"
    "bufio"
    "io"
)
/*
dynamic json https://gist.github.com/mbeale/4247971
golang map https://blog.golang.org/go-maps-in-action
go json example https://gobyexample.com/json
golang map prints out of order
http://stackoverflow.com/questions/12108215/golang-map-prints-out-of-order
*/

func main() {
    f, _ := os.Open("file.csv")

    r := csv.NewReader(bufio.NewReader(f))

    headers, err := r.Read()
    if err == io.EOF {
        os.Exit(1)
    }

    for {
        record, err := r.Read()
        if err == io.EOF {
            break
        }
        output_json := "{"
        for index:=0; index<len(headers)-1; index++ {
            output_json = output_json + "\"" + headers[index] + "\":" + record[index] + ","
        }
        output_json = output_json + "\"" + headers[len(headers)-1] + "\":" + record[len(headers)-1] + "}"
        fmt.Println(output_json)
    }
}
