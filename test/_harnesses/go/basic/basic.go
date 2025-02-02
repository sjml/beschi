package main

import (
	"flag"
	"io"
	"os"
	"path/filepath"

	"messages/comprehensive_message"
)

var ok bool = true

func softAssert(condition bool, label string) {
	if !condition {
		os.Stderr.WriteString("FAILED! Go: " + label + "\n")
		ok = false
	}
}

func main() {
	var example comprehensive_message.TestingMessage
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
	example.Ee = comprehensive_message.EnumeratedBeta
	example.Es = comprehensive_message.SpecifiedNegative
	example.S = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
	example.V2.X = 256.512
	example.V2.Y = 1024.768
	example.V3.X = 128.64
	example.V3.Y = 2048.4096
	example.V3.Z = 16.32
	example.C.R = 255
	example.C.G = 128
	example.C.B = 0
	example.Il = []int16{-1000, 500, 0, 750, 2000}
	example.El = []comprehensive_message.Specified{
		comprehensive_message.SpecifiedNegative,
		comprehensive_message.SpecifiedNegative,
		comprehensive_message.SpecifiedPositive,
		comprehensive_message.SpecifiedZero,
		comprehensive_message.SpecifiedPositive,
		comprehensive_message.SpecifiedZero,
	}
	example.Sl = []string{
		"Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
		"Quisque est eros, placerat ut libero ut, pellentesque tincidunt sem.",
		"Vivamus pellentesque turpis aliquet pretium tincidunt.",
		"Nulla facilisi.",
		"🐼❤️✝️",
		"用ねぼ雪入文モ段足リフケ報通ンさーを応細めい気川ヤセ車不古6治ニフサコ悩段をご青止ぽっ期年ト量報驚テルユ役1家埋詰軟きぎ。",
		"لآخر نشجب ونستنكر هؤلاء الرجال المفتونون بنشوة اللحظة الهائمون في رغبات",
	}
	var v21 comprehensive_message.Vec2
	v21.X = 10.0
	v21.Y = 15.0
	var v22 comprehensive_message.Vec2
	v22.X = 20.0
	v22.Y = 25.0
	var v23 comprehensive_message.Vec2
	v23.X = 30.0
	v23.Y = 35.0
	var v24 comprehensive_message.Vec2
	v24.X = 40.0
	v24.Y = 45.0
	example.V2l = []comprehensive_message.Vec2{v21, v22, v23, v24}
	var v31 comprehensive_message.Vec3
	v31.X = 10.0
	v31.Y = 15.0
	v31.Z = 17.5
	var v32 comprehensive_message.Vec3
	v32.X = 20.0
	v32.Y = 25.0
	v32.Z = 27.5
	var v33 comprehensive_message.Vec3
	v33.X = 30.0
	v33.Y = 35.0
	v33.Z = 37.5
	var v34 comprehensive_message.Vec3
	v34.X = 40.0
	v34.Y = 45.0
	v34.Z = 47.5
	example.V3l = []comprehensive_message.Vec3{v31, v32, v33, v34}
	var c1 comprehensive_message.Color
	c1.R = 255
	c1.G = 0
	c1.B = 0
	var c2 comprehensive_message.Color
	c2.R = 0
	c2.G = 255
	c2.B = 0
	var c3 comprehensive_message.Color
	c3.R = 0
	c3.G = 0
	c3.B = 255
	example.Cl = []comprehensive_message.Color{c1, c2, c3}
	example.Cx.Identifier = 127
	example.Cx.Label = "ComplexDataObject"
	example.Cx.BackgroundColor = c1
	example.Cx.TextColor = c2
	example.Cx.Spectrum = []comprehensive_message.Color{c3, c2, c1}
	example.Cx.Ranges = []comprehensive_message.Specified{
		comprehensive_message.SpecifiedNegative,
		comprehensive_message.SpecifiedPositive,
	}
	var cx1 comprehensive_message.ComplexData
	cx1.Identifier = 255
	cx1.Label = "Complex1"
	cx1.BackgroundColor = c3
	cx1.TextColor = c1
	cx1.Spectrum = []comprehensive_message.Color{c3, c2, c1, c2, c3}
	cx1.Ranges = []comprehensive_message.Specified{
		comprehensive_message.SpecifiedZero,
		comprehensive_message.SpecifiedPositive,
	}
	var cx2 comprehensive_message.ComplexData
	cx2.Identifier = 63
	cx2.Label = "Complex2"
	cx2.BackgroundColor = c1
	cx2.TextColor = c3
	cx2.Spectrum = []comprehensive_message.Color{c1, c2, c3, c2, c1}
	cx2.Ranges = []comprehensive_message.Specified{
		comprehensive_message.SpecifiedNegative,
		comprehensive_message.SpecifiedZero,
	}
	example.Cxl = []comprehensive_message.ComplexData{cx1, cx2}

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

		softAssert(example.GetSizeInBytes() == 956, "size calculation check")
		seek, _ := dat.Seek(0, io.SeekCurrent)
		softAssert(example.GetSizeInBytes() == (int)(seek), "written bytes check")
	} else if len(*readPathPtr) > 0 {
		dat, err := os.Open(*readPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		input, err := comprehensive_message.TestingMessageFromBytes(dat)
		softAssert(err == nil, "parsing test message")

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
		softAssert(len(input.Il) == len(example.Il), "[int16].length")
		for i := 0; i < len(input.Il); i++ {
			softAssert(input.Il[i] == example.Il[i], "[int16]")
		}
		softAssert((len(input.El) == len(example.El)), "[Specified].length")
		for i := 0; i < len(input.El); i++ {
			softAssert(input.El[i] == example.El[i], "[Specified]")
		}
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
		softAssert(len(input.Cx.Ranges) == len(example.Cx.Ranges), "ComplexData.ranges.length")
		for i := 0; i < len(input.Cx.Ranges); i++ {
			softAssert(input.Cx.Ranges[i] == example.Cx.Ranges[i], "ComplexData.ranges")
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
			softAssert(len(input.Cxl[i].Ranges) == len(example.Cxl[i].Ranges), "[ComplexData].ranges.length")
			for j := 0; j < len(input.Cxl[i].Ranges); j++ {
				softAssert(input.Cxl[i].Ranges[j] == example.Cxl[i].Ranges[j], "[ComplexData].ranges")
			}
		}

	}

	if !ok {
		os.Stderr.WriteString("Failed assertions.\n")
		os.Exit(1)
	}
}
