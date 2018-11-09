package job.fscience.com.lib;

import android.widget.OverScroller;

/**
 * ICS API access for ScrollerCompat
 */
class ScrollerCompatIcs {
    public static float getCurrVelocity(Object scroller) {
        return ((OverScroller) scroller).getCurrVelocity();
    }
}
