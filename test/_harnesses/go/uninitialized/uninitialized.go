package main

import (
	"flag"
	"os"
	"path/filepath"

	"messages/comprehensivemessage"
)

var ok bool = true

func softAssert(condition bool, label string) {
	if !condition {
		os.Stderr.WriteString("FAILED! Go: " + label + "\n")
		ok = false
	}
}

func main() {
	example := comprehensivemessage.NewTestingMessageDefault()

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

		example.WriteBytes(dat, false)
	} else if len(*readPathPtr) > 0 {
		dat, err := os.Open(*readPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		input, err := comprehensivemessage.TestingMessageFromBytes(dat)
		softAssert(err == nil, "parsing test message")
		softAssert(input != nil, "parsing test message")

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
		softAssert(input.Ee == example.Ee, "enumerated")
		softAssert(input.Es == example.Es, "specified")
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
		softAssert(input.Cx.Identifier == example.Cx.Identifier, "ComplexData.identifier")
		softAssert(input.Cx.Label == example.Cx.Label, "ComplexData.label")
		softAssert(input.Cx.BackgroundColor.R == example.Cx.BackgroundColor.R, "ComplexData.BackgroundColor.r")
		softAssert(input.Cx.BackgroundColor.G == example.Cx.BackgroundColor.G, "ComplexData.BackgroundColor.g")
		softAssert(input.Cx.BackgroundColor.B == example.Cx.BackgroundColor.B, "ComplexData.BackgroundColor.b")
		softAssert(input.Cx.TextColor.R == example.Cx.TextColor.R, "ComplexData.TextColor.r")
		softAssert(input.Cx.TextColor.G == example.Cx.TextColor.G, "ComplexData.TextColor.g")
		softAssert(input.Cx.TextColor.B == example.Cx.TextColor.B, "ComplexData.TextColor.b")
		softAssert(len(input.Cx.Spectrum) == len(example.Cx.Spectrum), "ComplexData.spectrum.length")
		for i := 0; i < len(input.Cx.Spectrum); i++ {
			softAssert(input.Cx.Spectrum[i].R == example.Cx.Spectrum[i].R, "ComplexData.spectrum.r")
			softAssert(input.Cx.Spectrum[i].G == example.Cx.Spectrum[i].G, "ComplexData.spectrum.g")
			softAssert(input.Cx.Spectrum[i].B == example.Cx.Spectrum[i].B, "ComplexData.spectrum.b")
		}
		softAssert(len(input.Cxl) == len(example.Cxl), "[ComplexData].length")
		for i := 0; i < len(input.Cxl); i++ {
			softAssert(input.Cxl[i].Identifier == example.Cxl[i].Identifier, "[ComplexData].identifier")
			softAssert(input.Cxl[i].Label == example.Cxl[i].Label, "[ComplexData].label")
			softAssert(input.Cxl[i].BackgroundColor.R == example.Cxl[i].BackgroundColor.R, "[ComplexData].backgroundColor.r")
			softAssert(input.Cxl[i].BackgroundColor.G == example.Cxl[i].BackgroundColor.G, "[ComplexData].backgroundColor.g")
			softAssert(input.Cxl[i].BackgroundColor.B == example.Cxl[i].BackgroundColor.B, "[ComplexData].backgroundColor.b")
			softAssert(input.Cxl[i].TextColor.R == example.Cxl[i].TextColor.R, "[ComplexData].textColor.r")
			softAssert(input.Cxl[i].TextColor.G == example.Cxl[i].TextColor.G, "[ComplexData].textColor.g")
			softAssert(input.Cxl[i].TextColor.B == example.Cxl[i].TextColor.B, "[ComplexData].textColor.b")
			softAssert(len(input.Cxl[i].Spectrum) == len(example.Cxl[i].Spectrum), "[ComplexData].spectrum.length")
			for j := 0; j < len(input.Cxl[i].Spectrum); j++ {
				softAssert(input.Cxl[i].Spectrum[j].R == example.Cxl[i].Spectrum[j].R, "[ComplexData].spectrum.r")
				softAssert(input.Cxl[i].Spectrum[j].G == example.Cxl[i].Spectrum[j].G, "[ComplexData].spectrum.g")
				softAssert(input.Cxl[i].Spectrum[j].B == example.Cxl[i].Spectrum[j].B, "[ComplexData].spectrum.b")
			}
		}

	}

	if !ok {
		os.Stderr.WriteString("Failed assertions.\n")
		os.Exit(1)
	}
}
