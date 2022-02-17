package main

import (
	"flag"
	"os"
	"path/filepath"

	"./src/WireMessage"
)

var ok bool

func softAssert(condition bool, label string) {
	if !condition {
		os.Stderr.WriteString("FAILED! " + label + "\n")
		ok = false
	}
}

func main() {
	var example WireMessage.TestingMessage
	example.B = 250
	example.Tf = true
	example.I16 = -32000
	example.Ui16 = 65000
	example.I32 = -2000000000
	example.Ui32 = 4000000000
	example.I64 = -9000000000000000000
	example.Ui64 = 18000000000000000000
	example.F = 3.1415927410125732421875
	example.D = 2.718281828459045090795598298427648842334747314453125
	example.S = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
	example.V2.X = 256.512
	example.V2.Y = 1024.768
	example.V3.X = 128.64
	example.V3.Y = 2048.4096
	example.V3.Z = 16.32
	example.C.R = 255
	example.C.G = 128
	example.C.B = 0
	example.Sl = []string{
		"Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
		"Quisque est eros, placerat ut libero ut, pellentesque tincidunt sem.",
		"Vivamus pellentesque turpis aliquet pretium tincidunt.",
		"Nulla facilisi.",
		"🐼❤️✝️",
	}
	var v21 WireMessage.Vec2
	v21.X = 10.0
	v21.Y = 15.0
	var v22 WireMessage.Vec2
	v22.X = 20.0
	v22.Y = 25.0
	var v23 WireMessage.Vec2
	v23.X = 30.0
	v23.Y = 35.0
	var v24 WireMessage.Vec2
	v24.X = 40.0
	v24.Y = 45.0
	example.V2l = []WireMessage.Vec2{v21, v22, v23, v24}
	var v31 WireMessage.Vec3
	v31.X = 10.0
	v31.Y = 15.0
	v31.Z = 17.5
	var v32 WireMessage.Vec3
	v32.X = 20.0
	v32.Y = 25.0
	v32.Z = 27.5
	var v33 WireMessage.Vec3
	v33.X = 30.0
	v33.Y = 35.0
	v33.Z = 37.5
	var v34 WireMessage.Vec3
	v34.X = 40.0
	v34.Y = 45.0
	v34.Z = 47.5
	example.V3l = []WireMessage.Vec3{v31, v32, v33, v34}
	var c1 WireMessage.Color
	c1.R = 255
	c1.G = 0
	c1.B = 0
	var c2 WireMessage.Color
	c2.R = 0
	c2.G = 255
	c2.B = 0
	var c3 WireMessage.Color
	c3.R = 0
	c3.G = 0
	c3.B = 255
	example.Cl = []WireMessage.Color{c1, c2, c3}

	readPathPtr := flag.String("read", "", "path to message file for verification")
	generatePathPtr := flag.String("generate", "", "path to message file for generation")
	flag.Parse()

	if len(*generatePathPtr) > 0 {
		os.MkdirAll(filepath.Dir(*generatePathPtr), os.ModePerm)
		dat, err := os.Create(*generatePathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		example.WriteBytes(dat)

	} else if len(*readPathPtr) > 0 {
		dat, err := os.Open(*readPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		var input WireMessage.TestingMessage
		WireMessage.TestingMessageFromBytes(dat, &input)

		ok = true
		softAssert(input.B == example.B, "byte")
		softAssert(input.Tf == example.Tf, "bool")
		softAssert(input.I16 == example.I16, "i16")
		softAssert(input.Ui16 == example.Ui16, "ui16")
		softAssert(input.I32 == example.I32, "i32")
		softAssert(input.Ui32 == example.Ui32, "ui32")
		softAssert(input.I64 == example.I64, "i64")
		softAssert(input.Ui64 == example.Ui64, "ui64")
		softAssert(input.F == example.F, "float")
		softAssert(input.D == example.D, "double")
		softAssert(input.S == example.S, "string")
		softAssert(input.V2.X == example.V2.X, "Vec2")
		softAssert(input.V2.Y == example.V2.Y, "Vec2")
		softAssert(input.V3.X == example.V3.X, "Vec3")
		softAssert(input.V3.Y == example.V3.Y, "Vec3")
		softAssert(input.V3.Z == example.V3.Z, "Vec3")
		softAssert(input.C.R == example.C.R, "Color")
		softAssert(input.C.G == example.C.G, "Color")
		softAssert(input.C.B == example.C.B, "Color")
		softAssert(len(input.Sl) == len(example.Sl), "[string].length")
		for i := 0; i < len(input.Sl); i++ {
			softAssert(input.Sl[i] == example.Sl[i], "[string]")
		}
		softAssert(len(input.V2l) == len(example.V2l), "[Vec2].length")
		for i := 0; i < len(input.V2l); i++ {
			softAssert(input.V2l[i].X == example.V2l[i].X, "[Vec2].x")
			softAssert(input.V2l[i].Y == example.V2l[i].Y, "[Vec2].y")
		}
		softAssert(len(input.V3l) == len(example.V3l), "[Vec3].length")
		for i := 0; i < len(input.V3l); i++ {
			softAssert(input.V3l[i].X == example.V3l[i].X, "[Vec3].x")
			softAssert(input.V3l[i].Y == example.V3l[i].Y, "[Vec3].y")
			softAssert(input.V3l[i].Z == example.V3l[i].Z, "[Vec3].z")
		}
		softAssert(len(input.Cl) == len(example.Cl), "[Color].length")
		for i := 0; i < len(input.Cl); i++ {
			softAssert(input.Cl[i].R == example.Cl[i].R, "[Color].r")
			softAssert(input.Cl[i].G == example.Cl[i].G, "[Color].g")
			softAssert(input.Cl[i].B == example.Cl[i].B, "[Color].b")
		}

		if !ok {
			os.Stderr.WriteString("Failed assertions.\n")
			os.Exit(1)
		}
	}
}
