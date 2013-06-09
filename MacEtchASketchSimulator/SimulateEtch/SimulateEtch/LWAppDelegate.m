//
//  LWAppDelegate.m
//  SimulateEtch
//
//  Created by Evan Long on 5/30/13.
//  Copyright (c) 2013 Evan. All rights reserved.
//

#import "LWAppDelegate.h"

@implementation LWAppDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
    self.window = [[NSWindow alloc] initWithContentRect:NSMakeRect(100, 100, 800, 700)
                                              styleMask:NSResizableWindowMask | NSMiniaturizableWindowMask | NSTitledWindowMask | NSClosableWindowMask
                                                backing:NSBackingStoreBuffered
                                                  defer:NO];
    [self.window makeKeyAndOrderFront:self];
    
    self.controller = [[LWViewController alloc] init];
    self.window.contentView = self.controller.view;
}

- (IBAction)open:(id)sender
{
    NSOpenPanel* panel = [NSOpenPanel openPanel];
    panel.canChooseDirectories = NO;
    panel.canChooseFiles = YES;
    panel.delegate = self;
    [panel runModal];
}

- (BOOL)panel:(id)sender validateURL:(NSURL *)url error:(NSError **)outError
{
    NSString* contents = [NSString stringWithContentsOfURL:url encoding:NSUTF8StringEncoding error:nil];
    [self.controller simulateEtchASketch:contents];
    
    return YES;
}

@end
