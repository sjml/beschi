using System;
using System.IO;

using AppMessages;

class ReadMeWriter {
    static void Main(string[] args) {
        var msg = new AppMessages.Vector3Message();
        msg.x = 1.0f;
        msg.y = 4096.1234f;
        msg.z = -42.56f;
        var fs = new FileStream("./vec3.msg", FileMode.Create);
        var bw = new BinaryWriter(fs);
        msg.WriteBytes(bw, false);
    }
}
