//
//  LWAppDelegate.h
//  SimulateEtch
//
//  Created by Evan Long on 5/30/13.
//  Copyright (c) 2013 Evan. All rights reserved.
//

#import <Cocoa/Cocoa.h>
#import "LWViewController.h"

@interface LWAppDelegate : NSObject <NSApplicationDelegate, NSOpenSavePanelDelegate>

@property (nonatomic, strong) NSWindow* window;
@property (nonatomic, strong) LWViewController* controller;

- (IBAction)open:(id)sender;

@end
