package com.elsewhere.parallelself;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;
import java.io.File;
import java.io.FileNotFoundException;

/** Read-only, temporary, per-URI granted PNG provider; no external library. */
public final class SharedImageProvider extends ContentProvider {
    @Override public boolean onCreate() { return true; }
    private File resolve(Uri uri) throws FileNotFoundException {
        String name=uri.getLastPathSegment();
        if(name==null || !name.matches("[a-f0-9]{32}\\.png")) throw new FileNotFoundException("invalid name");
        File file=new File(new File(getContext().getCacheDir(),"shared-images"),name);
        if(!file.isFile())throw new FileNotFoundException("missing image");
        return file;
    }
    @Override public ParcelFileDescriptor openFile(Uri uri,String mode) throws FileNotFoundException {
        if(!"r".equals(mode))throw new FileNotFoundException("read only");
        return ParcelFileDescriptor.open(resolve(uri),ParcelFileDescriptor.MODE_READ_ONLY);
    }
    @Override public String getType(Uri uri){return "image/png";}
    @Override public Cursor query(Uri uri,String[] projection,String selection,String[] args,String order){
        try{File file=resolve(uri);MatrixCursor cursor=new MatrixCursor(new String[]{OpenableColumns.DISPLAY_NAME,OpenableColumns.SIZE});cursor.addRow(new Object[]{"我的平行身份.png",file.length()});return cursor;}catch(FileNotFoundException e){return null;}
    }
    @Override public Uri insert(Uri uri,ContentValues values){throw new UnsupportedOperationException("read only");}
    @Override public int update(Uri uri,ContentValues values,String selection,String[] args){throw new UnsupportedOperationException("read only");}
    @Override public int delete(Uri uri,String selection,String[] args){throw new UnsupportedOperationException("read only");}
}
