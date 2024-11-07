// This file was automatically generated by Beschi v0.2.0
// <https://github.com/sjml/beschi>
// Do not edit directly.

package AppMessages

import (
	"encoding/binary"
	"fmt"
	"io"
)

func readString(data io.Reader, str *string) error {
	var len byte
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
	strLen := (byte)(len(*str))
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

type MessageType byte
const (
	Vector3MessageType MessageType = 1
	NewCharacterMessageType MessageType = 2
	CharacterJoinedTeamType MessageType = 3
)

type Message interface {
	GetMessageType() MessageType
	WriteBytes(data io.Writer, tag bool)
	GetSizeInBytes() int
}

func ProcessRawBytes(data io.Reader) ([]Message, error) {
	var msgList []Message
	var err error
	for err != io.EOF {
		var msgType MessageType
		err = binary.Read(data, binary.LittleEndian, &msgType)
		if err == io.EOF {
			break
		}
		if msgType == 0 {
			return msgList, nil
		}
		switch msgType {
		case Vector3MessageType:
			msg, err := Vector3MessageFromBytes(data)
			if err != nil {
				return nil, fmt.Errorf("Vector3Message read (%w)", err)
			}
			msgList = append(msgList, msg)
		case NewCharacterMessageType:
			msg, err := NewCharacterMessageFromBytes(data)
			if err != nil {
				return nil, fmt.Errorf("NewCharacterMessage read (%w)", err)
			}
			msgList = append(msgList, msg)
		case CharacterJoinedTeamType:
			msg, err := CharacterJoinedTeamFromBytes(data)
			if err != nil {
				return nil, fmt.Errorf("CharacterJoinedTeam read (%w)", err)
			}
			msgList = append(msgList, msg)
		default:
			return nil, fmt.Errorf("Unknown message type: %d", msgType)
		}
	}
	return msgList, nil
}

type Color struct {
	Red float32
	Green float32
	Blue float32
	Alpha float32
}

func ColorFromBytes(data io.Reader, input *Color) error {
	if err := binary.Read(data, binary.LittleEndian, &input.Red); err != nil {
		return fmt.Errorf("Could not read input.Red at offset %d (%w)", getDataOffset(data), err)
	}
	if err := binary.Read(data, binary.LittleEndian, &input.Green); err != nil {
		return fmt.Errorf("Could not read input.Green at offset %d (%w)", getDataOffset(data), err)
	}
	if err := binary.Read(data, binary.LittleEndian, &input.Blue); err != nil {
		return fmt.Errorf("Could not read input.Blue at offset %d (%w)", getDataOffset(data), err)
	}
	if err := binary.Read(data, binary.LittleEndian, &input.Alpha); err != nil {
		return fmt.Errorf("Could not read input.Alpha at offset %d (%w)", getDataOffset(data), err)
	}
	return nil
}

func (output Color) WriteBytes(data io.Writer) {
	binary.Write(data, binary.LittleEndian, &output.Red)
	binary.Write(data, binary.LittleEndian, &output.Green)
	binary.Write(data, binary.LittleEndian, &output.Blue)
	binary.Write(data, binary.LittleEndian, &output.Alpha)
}

type Spectrum struct {
	DefaultColor Color
	Colors []Color
}

func SpectrumFromBytes(data io.Reader, input *Spectrum) error {
	if err := binary.Read(data, binary.LittleEndian, &input.DefaultColor); err != nil {
		return fmt.Errorf("Could not read input.DefaultColor at offset %d (%w)", getDataOffset(data), err)
	}
	var Colors_Len uint16
	if err := binary.Read(data, binary.LittleEndian, &Colors_Len); err != nil {
		return fmt.Errorf("Could not read Colors_Len at offset %d (%w)", getDataOffset(data), err)
	}
	input.Colors = make([]Color, Colors_Len)
	for i1 := (uint16)(0); i1 < Colors_Len; i1++ {
		if err := binary.Read(data, binary.LittleEndian, &input.Colors[i1]); err != nil {
			return fmt.Errorf("Could not read input.Colors[i1] at offset %d (%w)", getDataOffset(data), err)
		}
	}
	return nil
}

func (output Spectrum) WriteBytes(data io.Writer) {
	binary.Write(data, binary.LittleEndian, &output.DefaultColor)
	Colors_Len := (uint16)(len(output.Colors))
	binary.Write(data, binary.LittleEndian, Colors_Len)
	for i1 := (uint16)(0); i1 < Colors_Len; i1++ {
		binary.Write(data, binary.LittleEndian, &output.Colors[i1])
	}
}

type Vector3Message struct {
	X float32
	Y float32
	Z float32
}

func (output Vector3Message) GetMessageType() MessageType {
	return Vector3MessageType
}

func (output Vector3Message) GetSizeInBytes() int {
	return 12
}
func Vector3MessageFromBytes(data io.Reader) (*Vector3Message, error) {
	msg := &Vector3Message{}

	if err := binary.Read(data, binary.LittleEndian, &msg.X); err != nil {
		return nil, fmt.Errorf("Could not read msg.X at offset %d (%w)", getDataOffset(data), err)
	}
	if err := binary.Read(data, binary.LittleEndian, &msg.Y); err != nil {
		return nil, fmt.Errorf("Could not read msg.Y at offset %d (%w)", getDataOffset(data), err)
	}
	if err := binary.Read(data, binary.LittleEndian, &msg.Z); err != nil {
		return nil, fmt.Errorf("Could not read msg.Z at offset %d (%w)", getDataOffset(data), err)
	}

	return msg, nil
}

func (output Vector3Message) WriteBytes(data io.Writer, tag bool) {
	if tag {
		binary.Write(data, binary.LittleEndian, Vector3MessageType)
	}
	binary.Write(data, binary.LittleEndian, &output.X)
	binary.Write(data, binary.LittleEndian, &output.Y)
	binary.Write(data, binary.LittleEndian, &output.Z)
}

type NewCharacterMessage struct {
	Id uint64
	CharacterName string
	Strength uint16
	Intelligence uint16
	Dexterity uint16
	GoldInWallet uint32
	Nicknames []string
}

func (output NewCharacterMessage) GetMessageType() MessageType {
	return NewCharacterMessageType
}

func (output NewCharacterMessage) GetSizeInBytes() int {
	size := 0
	size += len(output.CharacterName)
	for _, s := range output.Nicknames {
		size += 1 + len(s)
	}
	size += 21
	return size
}
func NewCharacterMessageFromBytes(data io.Reader) (*NewCharacterMessage, error) {
	msg := &NewCharacterMessage{}

	if err := binary.Read(data, binary.LittleEndian, &msg.Id); err != nil {
		return nil, fmt.Errorf("Could not read msg.Id at offset %d (%w)", getDataOffset(data), err)
	}
	if err := readString(data, &msg.CharacterName); err != nil {
		return nil, fmt.Errorf("Could not read string at offset %d (%w)", getDataOffset(data), err)
	}
	if err := binary.Read(data, binary.LittleEndian, &msg.Strength); err != nil {
		return nil, fmt.Errorf("Could not read msg.Strength at offset %d (%w)", getDataOffset(data), err)
	}
	if err := binary.Read(data, binary.LittleEndian, &msg.Intelligence); err != nil {
		return nil, fmt.Errorf("Could not read msg.Intelligence at offset %d (%w)", getDataOffset(data), err)
	}
	if err := binary.Read(data, binary.LittleEndian, &msg.Dexterity); err != nil {
		return nil, fmt.Errorf("Could not read msg.Dexterity at offset %d (%w)", getDataOffset(data), err)
	}
	if err := binary.Read(data, binary.LittleEndian, &msg.GoldInWallet); err != nil {
		return nil, fmt.Errorf("Could not read msg.GoldInWallet at offset %d (%w)", getDataOffset(data), err)
	}
	var Nicknames_Len uint16
	if err := binary.Read(data, binary.LittleEndian, &Nicknames_Len); err != nil {
		return nil, fmt.Errorf("Could not read Nicknames_Len at offset %d (%w)", getDataOffset(data), err)
	}
	msg.Nicknames = make([]string, Nicknames_Len)
	for i1 := (uint16)(0); i1 < Nicknames_Len; i1++ {
		if err := readString(data, &msg.Nicknames[i1]); err != nil {
			return nil, fmt.Errorf("Could not read string at offset %d (%w)", getDataOffset(data), err)
		}
	}

	return msg, nil
}

func (output NewCharacterMessage) WriteBytes(data io.Writer, tag bool) {
	if tag {
		binary.Write(data, binary.LittleEndian, NewCharacterMessageType)
	}
	binary.Write(data, binary.LittleEndian, &output.Id)
	writeString(data, &output.CharacterName)
	binary.Write(data, binary.LittleEndian, &output.Strength)
	binary.Write(data, binary.LittleEndian, &output.Intelligence)
	binary.Write(data, binary.LittleEndian, &output.Dexterity)
	binary.Write(data, binary.LittleEndian, &output.GoldInWallet)
	Nicknames_Len := (uint16)(len(output.Nicknames))
	binary.Write(data, binary.LittleEndian, Nicknames_Len)
	for i1 := (uint16)(0); i1 < Nicknames_Len; i1++ {
		writeString(data, &output.Nicknames[i1])
	}
}

type CharacterJoinedTeam struct {
	CharacterID uint64
	TeamName string
	TeamColors []Color
}

func (output CharacterJoinedTeam) GetMessageType() MessageType {
	return CharacterJoinedTeamType
}

func (output CharacterJoinedTeam) GetSizeInBytes() int {
	size := 0
	size += len(output.TeamName)
	size += len(output.TeamColors) * 16
	size += 11
	return size
}
func CharacterJoinedTeamFromBytes(data io.Reader) (*CharacterJoinedTeam, error) {
	msg := &CharacterJoinedTeam{}

	if err := binary.Read(data, binary.LittleEndian, &msg.CharacterID); err != nil {
		return nil, fmt.Errorf("Could not read msg.CharacterID at offset %d (%w)", getDataOffset(data), err)
	}
	if err := readString(data, &msg.TeamName); err != nil {
		return nil, fmt.Errorf("Could not read string at offset %d (%w)", getDataOffset(data), err)
	}
	var TeamColors_Len uint16
	if err := binary.Read(data, binary.LittleEndian, &TeamColors_Len); err != nil {
		return nil, fmt.Errorf("Could not read TeamColors_Len at offset %d (%w)", getDataOffset(data), err)
	}
	msg.TeamColors = make([]Color, TeamColors_Len)
	for i1 := (uint16)(0); i1 < TeamColors_Len; i1++ {
		if err := binary.Read(data, binary.LittleEndian, &msg.TeamColors[i1]); err != nil {
			return nil, fmt.Errorf("Could not read msg.TeamColors[i1] at offset %d (%w)", getDataOffset(data), err)
		}
	}

	return msg, nil
}

func (output CharacterJoinedTeam) WriteBytes(data io.Writer, tag bool) {
	if tag {
		binary.Write(data, binary.LittleEndian, CharacterJoinedTeamType)
	}
	binary.Write(data, binary.LittleEndian, &output.CharacterID)
	writeString(data, &output.TeamName)
	TeamColors_Len := (uint16)(len(output.TeamColors))
	binary.Write(data, binary.LittleEndian, TeamColors_Len)
	for i1 := (uint16)(0); i1 < TeamColors_Len; i1++ {
		binary.Write(data, binary.LittleEndian, &output.TeamColors[i1])
	}
}

