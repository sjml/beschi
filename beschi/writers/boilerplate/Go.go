package beschi

import (
	"encoding/binary"
	"fmt"
	"io"
)

func readString(data io.Reader, str *string) error {
	var len {# STRING_SIZE_TYPE #}
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
	strLen := ({# STRING_SIZE_TYPE #})(len(*str))
	binary.Write(data, binary.LittleEndian, strLen)
	io.WriteString(data, *str)
}

func getDataOffset(data io.Reader) int64 {
	if seeker, ok := data.(io.Seeker); ok {
		offset, _ := seeker.Seek(0, io.SeekCurrent)
		return offset
	}
	return -1
}

func GetPackedSize(msgList []Message) int {
	size := 0
	for _, msg := range msgList {
		size += msg.GetSizeInBytes()
	}
	size += len(msgList)
	size += 9
	return size
}

func PackMessages(msgList []Message, data io.Writer) {
	io.WriteString(data, "BSCI")
	binary.Write(data, binary.LittleEndian, uint32(len(msgList)))
	for _, msg := range msgList {
		msg.WriteBytes(data, true)
	}
	binary.Write(data, binary.LittleEndian, byte(0))
}

func UnpackMessages(data io.Reader) ([]Message, error) {
	sbytes := make([]byte, 4)
	err := binary.Read(data, binary.LittleEndian, &sbytes)
	if err != nil {
		panic(err)
	}
	if string(sbytes) != "BSCI" {
		return nil, fmt.Errorf("packed message buffer has invalid header")
	}
	var msgCount int32
	if err := binary.Read(data, binary.LittleEndian, &msgCount); err != nil {
		return nil, fmt.Errorf("could not read message count (%w)", err)
	}
	if msgCount == 0 {
		return []Message{}, nil
	}
	msgList, err := ProcessRawBytes(data, int(msgCount))
	if err != nil {
		return nil, fmt.Errorf("could not raw packed bytes (%w)", err)
	}
	if len(msgList) == 0 {
		return nil, fmt.Errorf("no messages in buffer")
	}
	if len(msgList) != int(msgCount) {
		return nil, fmt.Errorf("unexpected number of messages in buffer")
	}
	return msgList, nil;
}
