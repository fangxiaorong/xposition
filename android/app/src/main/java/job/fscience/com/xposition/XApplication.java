package job.fscience.com.xposition;

import android.app.AlarmManager;
import android.app.Application;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import job.fscience.com.net.ServerRequest;
import job.fscience.com.server.PositionService;

public class XApplication extends Application {

    private static Context context = null;

    @Override
    public void onCreate() {
        super.onCreate();

        XApplication.context = getApplicationContext();
    }

    private static class SingletonRequestHolder {
        private final static ServerRequest instance = new ServerRequest(XApplication.context);
    }
    public static ServerRequest getServerInstance() {
        return SingletonRequestHolder.instance;
    }
}
