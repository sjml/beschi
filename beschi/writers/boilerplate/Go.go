package Beschi

import (
	"encoding/binary"
	"io"
)

func readString(data io.Reader, str *string) error {
	var len uint32
	binary.Read(data, binary.LittleEndian, &len)
	sbytes := make([]byte, len)
	err := binary.Read(data, binary.LittleEndian, &sbytes)
	if err != nil {
		panic(err)
	}
	*str = string(sbytes)
	return err
}

func writeString(data io.Writer, str *string) {
	strLen := (uint32)(len(*str))
	binary.Write(data, binary.LittleEndian, strLen)
	io.WriteString(data, *str)
}
