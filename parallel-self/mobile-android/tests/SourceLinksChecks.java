import com.elsewhere.parallelself.SourceLinks;
public final class SourceLinksChecks {
  public static void main(String[] args) {
    String[] good={"https://commons.wikimedia.org/wiki/File:test.jpg","https://imgflip.com/meme/140080740/lebron-james--jr-smith","https://zh.moegirl.org.cn/%E4%B8%9C%E7%99%BE%E5%BE%80%E4%BA%8B","https://github.com/HalfSweetLemon/sbti-weapp","https://github.com:443/test"};
    String[] bad={"http://github.com/test","javascript:alert(1)","file:///etc/passwd","content://somewhere/private","intent://github.com/test","https://github.com.evil.example/test","https://evil.example/","https://name:password@github.com/test","https://github.com:8443/test"," https://github.com/test","https://github.com/test\n","https://127.0.0.1/","https://github.com./test",null};
    for(String url:good)if(SourceLinks.validatedHttps(url)==null)throw new AssertionError("Rejected approved source: "+url);
    for(String url:bad)if(SourceLinks.validatedHttps(url)!=null)throw new AssertionError("Accepted unsupported source: "+url);
    System.out.println("HTTPS source policy: "+good.length+" approved URLs accepted, "+bad.length+" unsupported/malformed URLs rejected");
  }
}
