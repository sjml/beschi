public class DataReadErrorException : Exception
{
    public DataReadErrorException() { }

    public DataReadErrorException(string msg)
        : base(msg) { }

    public DataReadErrorException(string msg, Exception inner)
        : base(msg, inner) { }
}

public class UnknownMessageTypeException : Exception
{
    public UnknownMessageTypeException() { }

    public UnknownMessageTypeException(string msg)
        : base(msg) { }

    public UnknownMessageTypeException(string msg, Exception inner)
        : base(msg, inner) { }
}

public abstract class Message
{
    abstract public MessageType GetMessageType();
    abstract public void WriteBytes(BinaryWriter bw, bool tag);
    abstract public int GetSizeInBytes();

    public static Message[] ProcessRawBytes(BinaryReader br, int max)
    {
        List<Message> msgList = new List<Message>();
        if (max == 0)
        {
            return msgList.ToArray();
        }
        while (br.BaseStream.Position < br.BaseStream.Length && (max < 0 || msgList.Count < max))
        {
            byte msgType = br.ReadByte();
            switch (msgType)
            {
                case 0:
                    return msgList.ToArray();
{# MESSAGE_TYPE_CASES #}
                default:
                    throw new UnknownMessageTypeException(String.Format("Unknown message type: {0}", msgType));
            }
        }
        return msgList.ToArray();
    }

    public static int GetPackedSize(ICollection<Message> msgList) {
        var size = 0;
        foreach (var msg in msgList)
        {
            size += msg.GetSizeInBytes();
        }
        size += msgList.Count;
        size += 9;
        return size;
    }

    public static void PackMessages(ICollection<Message> msgList, BinaryWriter bw)
    {
        byte[] headerBytes = System.Text.Encoding.UTF8.GetBytes("BSCI");
        bw.Write(headerBytes);

        bw.Write((uint)msgList.Count);
        foreach (var msg in msgList)
        {
            msg.WriteBytes(bw, true);
        }
        bw.Write((byte)0);
    }

    public static Message[] UnpackMessages(BinaryReader br)
    {
        byte[] headerLabel = br.ReadBytes(4);
        if (System.Text.Encoding.UTF8.GetString(headerLabel) != "BSCI")
        {
            throw new DataReadErrorException("Packed message buffer has invalid header.");
        }
        uint msgCount = br.ReadUInt32();
        if (msgCount == 0) {
            return Array.Empty<Message>();
        }
        Message[] msgList = Message.ProcessRawBytes(br, Convert.ToInt32(msgCount));
        if (msgList.Length == 0)
        {
            throw new DataReadErrorException("No messages in buffer.");
        }
        if (msgList.Length != msgCount)
        {
            throw new DataReadErrorException("Unexpected number of messages in buffer.");
        }
        return msgList;
    }
}

