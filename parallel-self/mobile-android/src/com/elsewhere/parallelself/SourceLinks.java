package com.elsewhere.parallelself;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

/** Only explicit user-selected, verified public source hosts may leave the app. */
public final class SourceLinks {
    private static final Set<String> ALLOWED = new HashSet<String>(Arrays.asList(
        "commons.wikimedia.org", "imgflip.com", "zh.moegirl.org.cn", "github.com"
    ));
    private SourceLinks() { }
    public static String validatedHttps(String raw) {
        if (raw == null || raw.length() > 4096 || !raw.equals(raw.trim())) return null;
        try {
            URI uri = new URI(raw);
            String host = uri.getHost();
            if (!"https".equalsIgnoreCase(uri.getScheme()) || uri.isOpaque() || host == null || uri.getRawUserInfo() != null) return null;
            if (uri.getPort() != -1 && uri.getPort() != 443) return null;
            if (!ALLOWED.contains(host.toLowerCase(Locale.ROOT))) return null;
            return uri.toASCIIString();
        } catch (URISyntaxException error) { return null; }
    }
}
