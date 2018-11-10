package job.fscience.com.xposition;

import android.app.Application;
import android.content.Context;
import com.tencent.bugly.crashreport.CrashReport;
import job.fscience.com.net.ServerRequest;

public class XApplication extends Application {

    private static Context context = null;

    @Override
    public void onCreate() {
        super.onCreate();

        XApplication.context = getApplicationContext();

        CrashReport.initCrashReport(getApplicationContext(), "771384f936", true);
    }

    private static class SingletonRequestHolder {
        private final static ServerRequest instance = new ServerRequest(XApplication.context);
    }
    public static ServerRequest getServerInstance() {
        return SingletonRequestHolder.instance;
    }
}
