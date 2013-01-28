//
//  LWViewController.m
//  EtchTouch
//
//  Created by Evan Long on 11/14/12.
//  Copyright (c) 2012 Hippo. All rights reserved.
//

#import "LWViewController.h"
#import "LWTouchDrawView.h"

@interface LWViewController ()

@end

@implementation LWViewController

- (void)_clear {
    [(LWTouchDrawView *)self.view clear];
}

- (void)_save {
    LWTouchDrawView *view = (LWTouchDrawView *)self.view;
    NSMutableString *s = [NSMutableString string];
    [s appendFormat:@"data="];
    for (NSValue *v in [view pointsDrawn]) {
        CGPoint p = [v CGPointValue];
        [s appendFormat:@"%d,%d\n", (int)p.x, (int)p.y];
    }
    NSMutableURLRequest *req = [[NSMutableURLRequest alloc] initWithURL:[NSURL URLWithString:@"http://evlong13inch.local:5000/draw"]];
    req.HTTPMethod = @"POST";
    req.HTTPBody = [s dataUsingEncoding:NSUTF8StringEncoding];
    [NSURLConnection sendAsynchronousRequest:req
                                       queue:[NSOperationQueue mainQueue]
                           completionHandler:^(NSURLResponse *resp, NSData *d, NSError *e) {
                           }];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    UIButton *clear = [UIButton buttonWithType:UIButtonTypeRoundedRect];
    clear.frame = CGRectMake(10.0f, 10.0f, 60.0f, 30.0f);
    [clear setTitle:@"Clear" forState:UIControlStateNormal];
    [clear addTarget:self action:@selector(_clear) forControlEvents:UIControlEventTouchUpInside];
    [self.view addSubview:clear];
    
    UIButton *save = [UIButton buttonWithType:UIButtonTypeRoundedRect];
    save.frame = CGRectMake(80.0f, 10.0f, 60.0f, 30.0f);
    [save setTitle:@"Save" forState:UIControlStateNormal];
    [save addTarget:self action:@selector(_save) forControlEvents:UIControlEventTouchUpInside];
    [self.view addSubview:save];
}

@end
