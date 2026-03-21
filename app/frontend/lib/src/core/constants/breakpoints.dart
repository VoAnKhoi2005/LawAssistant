class ScreenSize {
  static const double mobile = 600;
  static const double tablet = 900;
  static const double desktop = 1200;
  
  // Minimum page size
  static const double minWidth = 1024;
  static const double minHeight = 768;
}

class Breakpoints {
  final double width;
  
  const Breakpoints(this.width);
  
  bool get isMobile => width < ScreenSize.mobile;
  bool get isTablet => width >= ScreenSize.mobile && width < ScreenSize.desktop;
  bool get isDesktop => width >= ScreenSize.desktop;
  
  bool get showSidebar => width >= ScreenSize.tablet;
  bool get showDetailsSidebar => width >= ScreenSize.desktop;
}
